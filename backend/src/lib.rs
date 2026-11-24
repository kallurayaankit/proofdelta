use axum::{
    body::Bytes,
    extract::DefaultBodyLimit,
    http::{HeaderMap, HeaderValue, StatusCode},
    response::Html,
    routing::{get, post},
    Json, Router,
};
use serde_json::{json, Value};
use std::path::PathBuf;
use tower_http::{services::ServeDir, set_header::SetResponseHeaderLayer};

pub const AMOUNT_MINOR: u32 = 3900;

pub fn receipt() -> Value {
    json!({"mode":"simulation", "provider":"none", "charged":false,
        "unlocked":true, "currency":"AUD", "amount_minor":AMOUNT_MINOR})
}

async fn simulate(headers: HeaderMap, body: Bytes) -> Result<Json<Value>, (StatusCode, Json<Value>)> {
    if headers.get("X-ProofDelta-Simulation").and_then(|v| v.to_str().ok()) != Some("1") {
        return Err((StatusCode::BAD_REQUEST, Json(json!({"error":"explicit_simulation_required"}))));
    }
    if !body.is_empty() {
        return Err((StatusCode::BAD_REQUEST, Json(json!({"error":"no_payment_or_document_data_accepted"}))));
    }
    Ok(Json(receipt()))
}

pub fn app(dist: PathBuf) -> Router {
    let index = std::fs::read_to_string(dist.join("index.html"))
        .unwrap_or_else(|_| "<html><head></head><body>Run npm run build first.</body></html>".into())
        .replacen("</head>", "<meta name=\"proofdelta-service\" content=\"rust-local\"></head>", 1);
    Router::new()
        .route("/", get(move || async move { Html(index) }))
        .route("/api/health", get(|| async { Json(json!({"status":"ok","service":"proofdelta","mode":"simulation"})) }))
        .route("/api/config", get(|| async { Json(json!({"currency":"AUD","amount_minor":AMOUNT_MINOR,"payments":"simulation","pdf_processing":"browser-local"})) }))
        .route("/api/checkout/simulate", post(simulate))
        .fallback_service(ServeDir::new(dist))
        .layer(DefaultBodyLimit::max(1024))
        .layer(SetResponseHeaderLayer::overriding(axum::http::header::CACHE_CONTROL, HeaderValue::from_static("no-store")))
        .layer(SetResponseHeaderLayer::overriding(axum::http::header::X_CONTENT_TYPE_OPTIONS, HeaderValue::from_static("nosniff")))
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::{body::Body, http::Request};
    use http_body_util::BodyExt;
    use tower::ServiceExt;
    fn service() -> Router { app(PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../dist")) }
    async fn send(method: &str, path: &str, header: bool, body: &str) -> (StatusCode, String) {
        let mut request = Request::builder().method(method).uri(path);
        if header { request = request.header("X-ProofDelta-Simulation", "1"); }
        let response = service().oneshot(request.body(Body::from(body.to_owned())).unwrap()).await.unwrap();
        let status = response.status();
        let body = response.into_body().collect().await.unwrap().to_bytes();
        (status, String::from_utf8(body.to_vec()).unwrap())
    }
    #[tokio::test]
    async fn simulation_never_charges_and_is_repeatable() {
        for _ in 0..2 {
            let (status, body) = send("POST", "/api/checkout/simulate", true, "").await;
            assert_eq!(status, StatusCode::OK);
            let value: Value = serde_json::from_str(&body).unwrap();
            assert_eq!(value, receipt());
            assert_eq!(value["charged"], false);
        }
    }
    #[tokio::test]
    async fn rejects_unmarked_requests_and_document_payloads() {
        assert_eq!(send("POST", "/api/checkout/simulate", false, "").await.0, StatusCode::BAD_REQUEST);
        assert_eq!(send("POST", "/api/checkout/simulate", true, "%PDF-fictional").await.0, StatusCode::BAD_REQUEST);
        assert_eq!(send("POST", "/api/checkout/simulate", true, &"x".repeat(2048)).await.0, StatusCode::PAYLOAD_TOO_LARGE);
    }
    #[tokio::test]
    async fn no_live_payment_or_upload_routes() {
        assert_eq!(send("POST", "/api/paypal/capture", true, "").await.0, StatusCode::METHOD_NOT_ALLOWED);
        assert_eq!(send("POST", "/api/upload", true, "").await.0, StatusCode::METHOD_NOT_ALLOWED);
        assert_eq!(send("GET", "/api/checkout/simulate", false, "").await.0, StatusCode::METHOD_NOT_ALLOWED);
    }
    #[tokio::test]
    async fn configuration_and_local_frontend_contract() {
        let (status, body) = send("GET", "/api/config", false, "").await;
        assert_eq!(status, StatusCode::OK);
        let value: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(value["amount_minor"], 3900);
        assert_eq!(value["pdf_processing"], "browser-local");
        let (status, html) = send("GET", "/", false, "").await;
        assert_eq!(status, StatusCode::OK);
        assert!(html.contains("content=\"rust-local\""));
        assert!(html.contains("id=\"root\""));
        assert_eq!(send("GET", "/api/health", false, "").await.0, StatusCode::OK);
        assert_eq!(send("GET", "/../Cargo.toml", false, "").await.0, StatusCode::NOT_FOUND);
    }
}

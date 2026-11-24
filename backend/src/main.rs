use std::path::PathBuf;
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Local development only. No public bind and no live payment credentials.
    let dist = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../dist");
    if !dist.join("index.html").is_file() { return Err("Run npm run build from the repository root first".into()); }
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8787").await?;
    println!("ProofDelta Rust development service: http://127.0.0.1:8787 (simulation only)");
    axum::serve(listener, proofdelta_service::app(dist)).await?;
    Ok(())
}

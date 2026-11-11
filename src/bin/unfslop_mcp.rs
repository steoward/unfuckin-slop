use unfuckin_slop::mcp;

#[tokio::main]
async fn main() -> std::io::Result<()> {
    mcp::run().await
}

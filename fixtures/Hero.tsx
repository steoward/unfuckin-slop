export function Hero() {
  return (
    <div className="hero" onClick={() => open()} onPointerDown={() => down()}>
      <span className="kicker">New</span>
      <img src="/hero.png" />
      <h1>Elevate your workflow</h1>
      <p>Fast — quiet — expensive.</p>
      <a href="/docs">Click here</a>
      <p>Lorem ipsum dolor sit amet.</p>
    </div>
  );
}

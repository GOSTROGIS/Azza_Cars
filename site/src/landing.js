// Landing page entry: fonts and styles. The pages are static HTML so they load fast and index well.
// The hero showroom picks its vehicle inline in index.html, before the first paint.
import "@fontsource-variable/archivo/wdth.css";
import "@fontsource-variable/inter";
import "./landing.css";

// The showroom and turntable animate forever, so pause them while the hero is off screen.
const hero = document.querySelector(".hero");
if (hero && "IntersectionObserver" in window) {
  new IntersectionObserver(([e]) => hero.classList.toggle("is-offscreen", !e.isIntersecting)).observe(hero);
}

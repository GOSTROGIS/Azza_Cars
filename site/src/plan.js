// Plan page: the business plan and the car sharing and rental plan as two tabs.
// The address hash (#plan, #rental) picks the tab, so each tab can be linked and the back button works.
import "./landing.js";

const tablist = document.querySelector('[role="tablist"]');
const tabs = [...tablist.querySelectorAll('[role="tab"]')];

function show(focus) {
  const id = location.hash.slice(1);
  const tab = tabs.find((t) => t.getAttribute("aria-controls") === id) || tabs[0];
  for (const t of tabs) {
    const on = t === tab;
    t.setAttribute("aria-selected", on);
    t.tabIndex = on ? 0 : -1;
    document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
  }
  if (focus) tab.focus();
}

// Clicks and arrow keys both change the hash. The hashchange handler shows the tab.
const select = (tab, focus) => {
  location.hash = tab.getAttribute("aria-controls");
  if (focus) tab.focus();
};
tablist.addEventListener("click", (e) => {
  const t = e.target.closest('[role="tab"]');
  if (t) select(t);
});
// Arrow keys move between tabs, as the WAI-ARIA tabs pattern expects.
tablist.addEventListener("keydown", (e) => {
  const step = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
  if (step) select(tabs[(tabs.indexOf(document.activeElement) + step + tabs.length) % tabs.length], true);
});
addEventListener("hashchange", () => { show(); scrollTo(0, 0); });
show();

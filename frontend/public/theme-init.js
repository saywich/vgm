(() => {
  let preference = "system";
  try {
    const saved = localStorage.getItem("vertical-theme");
    if (saved === "light" || saved === "dark") preference = saved;
  } catch {}
  const dark =
    preference === "dark" ||
    (preference === "system" &&
      matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  document
    .querySelector('meta[name="theme-color"]')
    ?.setAttribute("content", dark ? "#121212" : "#fafafa");
})();

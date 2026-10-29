import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { Monitor, Moon, Sun } from "lucide-react";

type ThemePreference = "system" | "light" | "dark";
type Theme = "light" | "dark";

const ThemeContext = createContext<{
  preference: ThemePreference;
  setPreference: (value: ThemePreference) => void;
}>({ preference: "system", setPreference: () => {} });

function savedPreference(): ThemePreference {
  try {
    const value = localStorage.getItem("vertical-theme");
    if (value === "light" || value === "dark") return value;
  } catch {}
  return "system";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [preference, setPreference] =
    useState<ThemePreference>(savedPreference);
  const [systemTheme, setSystemTheme] = useState<Theme>(() =>
    matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
  );

  useEffect(() => {
    const media = matchMedia("(prefers-color-scheme: dark)");
    const changed = () => setSystemTheme(media.matches ? "dark" : "light");
    const stored = (event: StorageEvent) => {
      if (event.key === "vertical-theme" || event.key === null)
        setPreference(savedPreference());
    };
    media.addEventListener("change", changed);
    window.addEventListener("storage", stored);
    return () => {
      media.removeEventListener("change", changed);
      window.removeEventListener("storage", stored);
    };
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme =
      preference === "system" ? systemTheme : preference;
    const background = getComputedStyle(document.documentElement)
      .getPropertyValue("--page-background")
      .trim();
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute("content", background);
  }, [preference, systemTheme]);

  function changePreference(value: ThemePreference) {
    setPreference(value);
    try {
      localStorage.setItem("vertical-theme", value);
    } catch {}
  }

  return (
    <ThemeContext.Provider
      value={{ preference, setPreference: changePreference }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function ThemeSelect() {
  const { preference, setPreference } = useContext(ThemeContext);
  const Icon =
    preference === "system" ? Monitor : preference === "dark" ? Moon : Sun;

  return (
    <label className="theme-select">
      <Icon size={16} aria-hidden="true" />
      <select
        aria-label="Color theme"
        value={preference}
        onChange={(event) =>
          setPreference(event.target.value as ThemePreference)
        }
      >
        <option value="system">System</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
    </label>
  );
}

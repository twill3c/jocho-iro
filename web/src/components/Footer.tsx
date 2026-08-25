import { FOOTER_LINKS, FOOTER_NOTICE } from "@/lib/links";

export default function Footer() {
  return (
    <footer className="footer" id="footer">
      {FOOTER_LINKS.map((l, i) => (
        <span key={l.label}>
          {i > 0 && <span className="fsep">・</span>}
          <a href={l.href}>{l.label}</a>
          {l.label === "MIT License" && ` ${FOOTER_NOTICE}`}
        </span>
      ))}
    </footer>
  );
}

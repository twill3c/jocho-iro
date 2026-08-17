import { FOOTER_LINKS, FOOTER_NOTICE } from "@/lib/links";

export default function Footer() {
  return (
    <footer className="footer" id="footer">
      {FOOTER_NOTICE}
      {FOOTER_LINKS.map((l) => (
        <span key={l.label}>
          <span className="fsep">・</span>
          <a href={l.href}>{l.label}</a>
        </span>
      ))}
    </footer>
  );
}

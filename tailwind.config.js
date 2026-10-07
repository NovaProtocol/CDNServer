/** Tailwind config for the CDNServer dashboard. The design-language tokens live in
 *  the CDN kits (cdn/<lang>/tokens/*), so Tailwind is layout utilities only. */
module.exports = {
  content: ["./templates/**/*.html", "./apps/**/*.py"],
  theme: {
    extend: {
      fontFamily: {
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
};

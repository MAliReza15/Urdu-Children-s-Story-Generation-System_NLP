import { Link } from "react-router-dom";

const FooterCTA = () => {
  return (
    <section className="py-24 bg-background">
      <div className="max-w-3xl mx-auto px-6 text-center">
        <h2 className="text-4xl md:text-5xl font-bold text-foreground leading-tight text-balance animate-fade-in-up">
          Ready to generate Urdu stories?
        </h2>
        <p className="mt-4 text-muted-foreground text-lg animate-fade-in-up" style={{ animationDelay: "0.1s", opacity: 0 }}>
          Try the trigram-powered story generator — built from scratch with real Urdu data.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4 animate-fade-in-up" style={{ animationDelay: "0.2s", opacity: 0 }}>
          <Link
            to="/chat"
            className="bg-primary text-primary-foreground px-7 py-3.5 rounded-full text-sm font-medium hover:opacity-90 transition-opacity hover:scale-105 transform duration-200"
          >
            Generate a Story
          </Link>
        </div>
      </div>

      <footer className="mt-24 border-t border-border pt-8 max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="text-lg">📖</span>
            <span className="font-semibold text-foreground">Urdu Story AI</span>
          </div>
          <p>© 2026 Urdu Story AI. All rights reserved.</p>
        </div>
      </footer>
    </section>
  );
};

export default FooterCTA;

import { Link } from "react-router-dom";

const HeroSection = () => {
  return (
    <section className="relative pt-32 pb-16 overflow-hidden brown-cloud-bg">
      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
        <h1 className="text-5xl md:text-7xl font-bold text-foreground leading-[1.1] tracking-tight text-balance animate-fade-in-up">
          Urdu Children's Story Generation
        </h1>
        <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: "0.1s", opacity: 0 }}>
          A genAI system that generates short Urdu stories for children — powered by BPE tokenization and trigram language modeling with real-world scraped data.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4 animate-fade-in-up" style={{ animationDelay: "0.2s", opacity: 0 }}>
          <Link
            to="/chat"
            className="bg-primary text-primary-foreground px-7 py-3.5 rounded-full text-sm font-medium hover:opacity-90 transition-opacity hover:scale-105 transform duration-200"
          >
            Generate a Story
          </Link>
          <a
            href="#features"
            className="border border-border bg-card text-foreground px-7 py-3.5 rounded-full text-sm font-medium hover:bg-secondary transition-colors hover:scale-105 transform duration-200"
          >
            How it works
          </a>
        </div>
      </div>

      {/* Trust bar */}
      <div className="relative z-10 mt-16 text-center animate-fade-in-up" style={{ animationDelay: "0.3s", opacity: 0 }}>
        <p className="text-sm text-muted-foreground">
          Built with <strong className="text-foreground">BPE Tokenization</strong> · <strong className="text-foreground">Trigram LM</strong> · <strong className="text-foreground">200+ Urdu Stories</strong>
        </p>
      </div>
    </section>
  );
};

export default HeroSection;

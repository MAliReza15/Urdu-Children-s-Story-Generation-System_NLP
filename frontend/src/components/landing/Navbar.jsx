import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-card/80 backdrop-blur-md border-b border-border animate-fade-in-down">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-xl">📖</span>
          <span className="text-lg font-bold text-foreground">Urdu Story AI</span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">How It Works</a>
          <Link to="/chat" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Generate Story</Link>
        </div>

        <Link
          to="/chat"
          className="bg-primary text-primary-foreground px-5 py-2.5 rounded-full text-sm font-medium hover:opacity-90 transition-opacity"
        >
          Try it now
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;

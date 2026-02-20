import { Link } from "react-router-dom";
import { Database, Scissors, BarChart3, Globe, MessageCircle, Rocket } from "lucide-react";

const features = [
  {
    icon: Database,
    title: "Dataset Collection",
    description: "Scrapes 200+ diverse Urdu children's stories, removes HTML/ads, normalizes Unicode, and standardizes punctuation.",
  },
  {
    icon: Scissors,
    title: "BPE Tokenization",
    description: "Custom Byte Pair Encoding tokenizer trained from scratch with a vocabulary size of 250, handling Urdu script efficiently.",
  },
  {
    icon: BarChart3,
    title: "Trigram Language Model",
    description: "3-gram model using Maximum Likelihood Estimation with interpolation for smooth, coherent text generation.",
  },
  {
    icon: Globe,
    title: "Urdu Script Support",
    description: "Full right-to-left Urdu text support with special tokens for sentence, paragraph, and story boundaries.",
  },
  {
    icon: MessageCircle,
    title: "ChatGPT-like Interface",
    description: "Interactive chat UI where you can prompt the model and receive generated Urdu stories in real time.",
  },
  {
    icon: Rocket,
    title: "Containerized Microservice",
    description: "Inference served via a containerized API microservice, deployed and accessible through a clean web interface.",
  },
];

const FeaturesSection = () => {
  return (
    <section id="features" className="py-24 bg-card">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16 animate-fade-in-up" style={{ opacity: 0 }}>
          <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">How It Works</p>
          <h2 className="text-4xl md:text-5xl font-bold text-foreground leading-tight text-balance">
            From raw data<br />to generated stories
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <div
              key={feature.title}
              className="border border-border rounded-2xl p-7 hover:shadow-2xl hover:shadow-primary/10 transition-all bg-card hover:scale-105 hover:-translate-y-2 transform duration-300 animate-fade-in-up relative overflow-hidden group"
              style={{ animationDelay: `${i * 0.1}s`, opacity: 0 }}
            >
              {/* 3D Card Background Effect */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/0 via-accent/0 to-primary/0 group-hover:from-primary/5 group-hover:via-accent/5 group-hover:to-primary/5 transition-all duration-300 rounded-2xl"></div>
              <div className="relative z-10">
                <div className="h-10 w-10 rounded-xl bg-secondary flex items-center justify-center mb-5 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300">
                  <feature.icon className="h-5 w-5 text-foreground" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-12 animate-fade-in-up" style={{ animationDelay: "0.6s", opacity: 0 }}>
          <Link
            to="/chat"
            className="bg-primary text-primary-foreground px-7 py-3.5 rounded-full text-sm font-medium hover:opacity-90 transition-opacity inline-block hover:scale-105 transform duration-200"
          >
            Generate a Story
          </Link>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;

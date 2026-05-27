import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Brain, Sparkles, Shield, Lock, Droplets } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#faf8f7] text-foreground font-sans selection:bg-primary/30">
      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center min-h-[80vh] px-4 overflow-hidden">
        {/* Decorative background elements */}
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-pink-200/20 rounded-full blur-3xl mix-blend-multiply" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-rose-200/20 rounded-full blur-3xl mix-blend-multiply" />

        <div className="z-10 text-center space-y-6 max-w-3xl">
          <p className="text-xl md:text-2xl text-muted-foreground/80 font-medium tracking-wide">
            Do you know?
          </p>
          <h1 className="text-6xl md:text-8xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-rose-400 to-pink-300 pb-2">
            DermaFlow AI.
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground mt-4 font-light">
            Your skin speaks. We help you understand.
          </p>
        </div>

        {/* Tip Card */}
        <div className="z-10 mt-16 bg-white/60 backdrop-blur-xl border border-white/40 shadow-xl rounded-3xl p-6 flex items-start gap-4 max-w-md w-full animate-in slide-in-from-bottom-8 duration-1000">
          <div className="bg-blue-100/50 p-3 rounded-2xl shrink-0">
            <Droplets className="w-8 h-8 text-blue-400" />
          </div>
          <div>
            <h3 className="font-semibold text-rose-400 text-lg">
              Hydration affects skin elasticity
            </h3>
            <p className="text-muted-foreground mt-1">
              Water is essential for healthy skin
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 bg-white/40 backdrop-blur-sm border-t border-white/20">
        <div className="max-w-6xl mx-auto space-y-16">
          <h2 className="text-4xl font-semibold text-center text-foreground/80 tracking-tight">
            Meet Your Own Derma Assistant
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white/80 backdrop-blur-md border border-white p-8 rounded-3xl shadow-sm hover:shadow-md transition-shadow">
              <div className="bg-rose-100/50 w-14 h-14 rounded-2xl flex items-center justify-center mb-6">
                <Brain className="w-7 h-7 text-rose-400" />
              </div>
              <h3 className="text-xl font-medium mb-3 text-foreground/90">AI-powered analysis</h3>
              <p className="text-muted-foreground leading-relaxed">
                Advanced algorithms trained on dermatological expertise
              </p>
            </div>

            <div className="bg-white/80 backdrop-blur-md border border-white p-8 rounded-3xl shadow-sm hover:shadow-md transition-shadow">
              <div className="bg-pink-100/50 w-14 h-14 rounded-2xl flex items-center justify-center mb-6">
                <Sparkles className="w-7 h-7 text-pink-400" />
              </div>
              <h3 className="text-xl font-medium mb-3 text-foreground/90">Personalized insights</h3>
              <p className="text-muted-foreground leading-relaxed">
                Tailored recommendations for your unique skin
              </p>
            </div>

            <div className="bg-white/80 backdrop-blur-md border border-white p-8 rounded-3xl shadow-sm hover:shadow-md transition-shadow">
              <div className="bg-red-100/50 w-14 h-14 rounded-2xl flex items-center justify-center mb-6">
                <Shield className="w-7 h-7 text-red-400" />
              </div>
              <h3 className="text-xl font-medium mb-3 text-foreground/90">Reliable medical information</h3>
              <p className="text-muted-foreground leading-relaxed">
                Backed by trusted dermatology research
              </p>
            </div>

            <div className="bg-white/80 backdrop-blur-md border border-white p-8 rounded-3xl shadow-sm hover:shadow-md transition-shadow">
              <div className="bg-rose-100/50 w-14 h-14 rounded-2xl flex items-center justify-center mb-6">
                <Lock className="w-7 h-7 text-rose-400" />
              </div>
              <h3 className="text-xl font-medium mb-3 text-foreground/90">Privacy-first assistant</h3>
              <p className="text-muted-foreground leading-relaxed">
                Your data stays secure and confidential
              </p>
            </div>
          </div>

          <div className="flex justify-center pt-8">
            <Link href="/chat">
              <Button className="bg-gradient-to-r from-rose-400 to-pink-400 hover:from-rose-500 hover:to-pink-500 text-white rounded-full px-12 py-7 text-xl shadow-xl shadow-rose-200/50 hover:shadow-rose-200 hover:scale-105 transition-all duration-300 font-medium border-0">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

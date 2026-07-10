import { About } from "@/views/home/about";
import { Contact } from "@/views/home/contact";
import { Experience } from "@/views/home/experience";
import { Footer } from "@/views/home/footer";
import { Hero } from "@/views/home/hero";
import { Nav } from "@/views/home/nav";
import { Projects } from "@/views/home/projects";
import { Publications } from "@/views/home/publications";
import { Research } from "@/views/home/research";

/**
 * Home view — Server Component. Sections are client leaves where animation
 * or interaction is required, keeping this file itself server-rendered
 * (hard rule #7).
 */
export const HomeView = () => {
  return (
    <main className="min-h-lvh">
      <Nav />
      <Hero />
      <About />
      <Research />
      <Projects />
      <Publications />
      <Experience />
      <Contact />
      <Footer />
    </main>
  );
};

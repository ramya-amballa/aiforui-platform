import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Eyebrow } from "@/components/ui/eyebrow";

export default function NotFound() {
  return (
    <section className="py-section-lg">
      <Container size="wide">
        <Eyebrow>404</Eyebrow>
        <h1 className="mt-6 font-serif text-display text-ink">[Not Found Title Placeholder]</h1>
        <p className="mt-6 max-w-xl text-base leading-relaxed text-muted">[Not Found Description Placeholder]</p>
        <div className="mt-10">
          <Button href="/" variant="primary" size="lg">
            [Return Home Placeholder]
          </Button>
        </div>
      </Container>
    </section>
  );
}

import type { NavItem } from "@/types";

export const site = {
  name: "AIforU&I",
  advisorName: "Ramya Amballa",
  tagline: "Independent advisory in AI, digital, cyber and technology risk governance.",
  description:
    "AIforU&I is an independent advisory practice founded by Ramya Amballa, focused on AI governance, digital governance, cyber governance, technology risk and third-party governance for regulated and high-assurance organisations.",
  url: "https://aiforui.org",
  locale: "en_US",
  twitter: "",
  email: "amballa.ramya911@gmail.com",
  linkedin: "https://www.linkedin.com/in/amballa-ramya/",
  substack: "https://aiforui.substack.com",
  github: "https://github.com/ramya-amballa",
  gumroad: "https://ramyavibes2.gumroad.com",
} as const;

export const primaryNav: NavItem[] = [
  { label: "Home", href: "/" },
  { label: "Methodology", href: "/methodology" },
  { label: "Selected Engagement Areas", href: "/selected-advisory-engagements" },
  { label: "Governance Domains", href: "/governance-domains" },
  { label: "Insights", href: "/insights" },
  { label: "Resources", href: "/resources" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

export const footerNav: { title: string; items: NavItem[] }[] = [
  {
    title: "Practice",
    items: [
      { label: "Methodology", href: "/methodology" },
      { label: "Selected Engagement Areas", href: "/selected-advisory-engagements" },
      { label: "Governance Domains", href: "/governance-domains" },
    ],
  },
  {
    title: "Perspective",
    items: [
      { label: "Insights", href: "/insights" },
      { label: "Resources", href: "/resources" },
    ],
  },
  {
    title: "Firm",
    items: [
      { label: "About", href: "/about" },
      { label: "Contact", href: "/contact" },
    ],
  },
];

export const primaryCta: NavItem = {
  label: "Selected Engagement Areas",
  href: "/selected-advisory-engagements",
};

export const secondaryCta: NavItem = {
  label: "Start a Conversation",
  href: "/contact",
};

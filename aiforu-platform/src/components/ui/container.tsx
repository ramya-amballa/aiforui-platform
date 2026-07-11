import { cn } from "@/lib/utils";

type ContainerSize = "default" | "narrow" | "wide";

const sizeMap: Record<ContainerSize, string> = {
  default: "max-w-shell",
  narrow: "max-w-3xl",
  wide: "max-w-[96rem]",
};

type ContainerTag = "div" | "section" | "header" | "footer" | "article" | "aside" | "main";

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: ContainerSize;
  as?: ContainerTag;
}

export function Container({ size = "default", as: Tag = "div", className, ...props }: ContainerProps) {
  return (
    <Tag
      className={cn("mx-auto w-full px-5 sm:px-8 lg:px-12", sizeMap[size], className)}
      {...props}
    />
  );
}

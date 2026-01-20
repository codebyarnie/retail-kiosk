// frontend/src/components/ui/__tests__/LoadingSkeleton.test.tsx
import { render } from '@testing-library/react';
import {
  Skeleton,
  ProductCardSkeleton,
  ListItemSkeleton,
  TextSkeleton,
} from '../LoadingSkeleton';

describe('Skeleton', () => {
  it('renders with animate-pulse class', () => {
    const { container } = render(<Skeleton />);
    const skeleton = container.firstChild as HTMLElement;

    expect(skeleton).toHaveClass('animate-pulse');
  });

  it('renders with bg-gray-200 class', () => {
    const { container } = render(<Skeleton />);
    const skeleton = container.firstChild as HTMLElement;

    expect(skeleton).toHaveClass('bg-gray-200');
  });

  it('renders with rounded class', () => {
    const { container } = render(<Skeleton />);
    const skeleton = container.firstChild as HTMLElement;

    expect(skeleton).toHaveClass('rounded');
  });

  it('applies custom className', () => {
    const { container } = render(<Skeleton className="w-full h-10" />);
    const skeleton = container.firstChild as HTMLElement;

    expect(skeleton).toHaveClass('w-full');
    expect(skeleton).toHaveClass('h-10');
  });
});

describe('ProductCardSkeleton', () => {
  it('renders skeleton structure', () => {
    const { container } = render(<ProductCardSkeleton />);

    // Should have the card container
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('bg-white');
    expect(card).toHaveClass('rounded-xl');
    expect(card).toHaveClass('border');

    // Should have multiple skeleton elements (image, title, description, price)
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThanOrEqual(4);
  });

  it('renders image skeleton with correct dimensions', () => {
    const { container } = render(<ProductCardSkeleton />);

    // Image skeleton should be w-full h-40
    const imageSkeleton = container.querySelector('.w-full.h-40');
    expect(imageSkeleton).toBeInTheDocument();
  });

  it('renders title skeleton', () => {
    const { container } = render(<ProductCardSkeleton />);

    // Title skeleton should be h-4 w-3/4
    const titleSkeleton = container.querySelector('.h-4.w-3\\/4');
    expect(titleSkeleton).toBeInTheDocument();
  });

  it('renders description skeleton', () => {
    const { container } = render(<ProductCardSkeleton />);

    // Description skeleton should be h-3 w-1/2
    const descSkeleton = container.querySelector('.h-3.w-1\\/2');
    expect(descSkeleton).toBeInTheDocument();
  });

  it('renders price skeleton', () => {
    const { container } = render(<ProductCardSkeleton />);

    // Price skeleton should be h-8 w-20
    const priceSkeleton = container.querySelector('.h-8.w-20');
    expect(priceSkeleton).toBeInTheDocument();
  });
});

describe('ListItemSkeleton', () => {
  it('renders skeleton structure', () => {
    const { container } = render(<ListItemSkeleton />);

    // Should have flex container
    const listItem = container.firstChild as HTMLElement;
    expect(listItem).toHaveClass('flex');
    expect(listItem).toHaveClass('items-center');
    expect(listItem).toHaveClass('gap-4');
  });

  it('renders thumbnail skeleton', () => {
    const { container } = render(<ListItemSkeleton />);

    // Thumbnail skeleton should be w-16 h-16 rounded-lg
    const thumbnail = container.querySelector('.w-16.h-16.rounded-lg');
    expect(thumbnail).toBeInTheDocument();
    expect(thumbnail).toHaveClass('animate-pulse');
  });

  it('renders title skeleton', () => {
    const { container } = render(<ListItemSkeleton />);

    // Title skeleton should be h-4 w-3/4
    const titleSkeleton = container.querySelector('.h-4.w-3\\/4');
    expect(titleSkeleton).toBeInTheDocument();
  });

  it('renders subtitle skeleton', () => {
    const { container } = render(<ListItemSkeleton />);

    // Subtitle skeleton should be h-3 w-1/4
    const subtitleSkeleton = container.querySelector('.h-3.w-1\\/4');
    expect(subtitleSkeleton).toBeInTheDocument();
  });

  it('renders action skeleton', () => {
    const { container } = render(<ListItemSkeleton />);

    // Action skeleton should be h-8 w-16
    const actionSkeleton = container.querySelector('.h-8.w-16');
    expect(actionSkeleton).toBeInTheDocument();
  });
});

describe('TextSkeleton', () => {
  it('renders with h-4 class', () => {
    const { container } = render(<TextSkeleton />);
    const skeleton = container.firstChild as HTMLElement;

    expect(skeleton).toHaveClass('h-4');
  });

  it('renders with animate-pulse class', () => {
    const { container } = render(<TextSkeleton />);
    const skeleton = container.firstChild as HTMLElement;

    expect(skeleton).toHaveClass('animate-pulse');
  });

  it('applies custom className', () => {
    const { container } = render(<TextSkeleton className="w-1/2" />);
    const skeleton = container.firstChild as HTMLElement;

    expect(skeleton).toHaveClass('w-1/2');
    expect(skeleton).toHaveClass('h-4');
  });
});

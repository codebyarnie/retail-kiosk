// frontend/src/components/ui/LoadingSkeleton.tsx
import classNames from 'classnames';

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={classNames(
        'animate-pulse bg-gray-200 rounded',
        className
      )}
    />
  );
}

export function ProductCardSkeleton() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <Skeleton className="w-full h-40 mb-4" />
      <Skeleton className="h-4 w-3/4 mb-2" />
      <Skeleton className="h-3 w-1/2 mb-4" />
      <Skeleton className="h-8 w-20" />
    </div>
  );
}

export function ListItemSkeleton() {
  return (
    <div className="flex items-center gap-4 py-4">
      <Skeleton className="w-16 h-16 rounded-lg" />
      <div className="flex-1">
        <Skeleton className="h-4 w-3/4 mb-2" />
        <Skeleton className="h-3 w-1/4" />
      </div>
      <Skeleton className="h-8 w-16" />
    </div>
  );
}

export function TextSkeleton({ className }: SkeletonProps) {
  return <Skeleton className={classNames('h-4', className)} />;
}

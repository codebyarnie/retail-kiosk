// frontend/src/components/ui/Button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react';
import classNames from 'classnames';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium rounded-lg ' +
      'transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 ' +
      'disabled:opacity-50 disabled:pointer-events-none touch-target';

    const variants = {
      primary:
        'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
      secondary:
        'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
      outline:
        'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 ' +
        'focus:ring-primary-500',
      ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    return (
      <button
        ref={ref}
        className={classNames(
          baseStyles,
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

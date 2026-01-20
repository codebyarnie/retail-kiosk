// Verify test setup works correctly
import { describe, it, expect } from 'vitest';

describe('Test Setup', () => {
  it('should have localStorage mock available', () => {
    expect(window.localStorage).toBeDefined();
    expect(window.localStorage.getItem).toBeDefined();
    expect(window.localStorage.setItem).toBeDefined();
  });

  it('should have matchMedia mock available', () => {
    expect(window.matchMedia).toBeDefined();
    const result = window.matchMedia('(min-width: 768px)');
    expect(result.matches).toBe(false);
    expect(result.media).toBe('(min-width: 768px)');
  });

  it('should support jest-dom matchers', () => {
    const element = document.createElement('div');
    element.textContent = 'Hello';
    document.body.appendChild(element);
    expect(element).toBeInTheDocument();
    document.body.removeChild(element);
  });
});

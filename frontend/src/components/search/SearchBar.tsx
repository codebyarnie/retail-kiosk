// frontend/src/components/search/SearchBar.tsx
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSearchStore } from '@/store';
import { useDebounce } from '@/hooks/useDebounce';

interface SearchBarProps {
  size?: 'default' | 'large';
  autoFocus?: boolean;
}

export function SearchBar({ size = 'default', autoFocus = false }: SearchBarProps) {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const { query, setQuery, suggestions, fetchSuggestions } = useSearchStore();
  const [localQuery, setLocalQuery] = useState(query);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debouncedQuery = useDebounce(localQuery, 300);

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  useEffect(() => {
    if (debouncedQuery) {
      void fetchSuggestions(debouncedQuery);
    }
  }, [debouncedQuery, fetchSuggestions]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (localQuery.trim()) {
      setQuery(localQuery);
      setShowSuggestions(false);
      navigate(`/search?q=${encodeURIComponent(localQuery)}`);
    }
  };

  const handleSuggestionClick = (text: string) => {
    setLocalQuery(text);
    setQuery(text);
    setShowSuggestions(false);
    navigate(`/search?q=${encodeURIComponent(text)}`);
  };

  const inputClasses = size === 'large'
    ? 'text-xl py-4 px-6'
    : 'text-base py-2 px-4';

  return (
    <form onSubmit={handleSubmit} className="relative w-full">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={localQuery}
          onChange={(e) => {
            setLocalQuery(e.target.value);
            setShowSuggestions(true);
          }}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder="Search for products..."
          className={`w-full bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none ${inputClasses}`}
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-primary-600 touch-target"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
      </div>

      {/* Suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-lg z-10 overflow-hidden">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              type="button"
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 touch-target"
              onClick={() => handleSuggestionClick(suggestion.text)}
            >
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span className="text-gray-700">{suggestion.text}</span>
              <span className="ml-auto text-xs text-gray-400 capitalize">{suggestion.type}</span>
            </button>
          ))}
        </div>
      )}
    </form>
  );
}

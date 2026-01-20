// frontend/src/components/search/SearchHero.tsx
import { SearchBar } from './SearchBar';

export function SearchHero() {
  return (
    <div className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-16 px-4">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-4">
          Find What You Need
        </h1>
        <p className="text-primary-100 text-lg mb-8">
          Search thousands of products or browse by category
        </p>
        <div className="max-w-xl mx-auto">
          <SearchBar size="large" autoFocus />
        </div>
      </div>
    </div>
  );
}

#!/usr/bin/env node

/**
 * Frontend Installation Verification Script
 *
 * This script verifies that all frontend dependencies are properly installed
 * and that the application can build successfully.
 *
 * Usage:
 *   node verify_installation.js
 *
 * Exit codes:
 *   0 - All checks passed
 *   1 - One or more checks failed
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ANSI color codes for terminal output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkNodeVersion() {
  log('\n📦 Checking Node.js version...', 'blue');
  try {
    const version = process.version;
    const majorVersion = parseInt(version.slice(1).split('.')[0]);

    if (majorVersion >= 18) {
      log(`✓ Node.js ${version} (meets requirement: >=18.0.0)`, 'green');
      return true;
    } else {
      log(`✗ Node.js ${version} (requires: >=18.0.0)`, 'red');
      return false;
    }
  } catch (error) {
    log(`✗ Error checking Node.js version: ${error.message}`, 'red');
    return false;
  }
}

function checkPackageJson() {
  log('\n📄 Checking package.json...', 'blue');
  try {
    const packagePath = path.join(__dirname, 'package.json');
    if (!fs.existsSync(packagePath)) {
      log('✗ package.json not found', 'red');
      return false;
    }

    const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    log('✓ package.json found and valid', 'green');

    // Check for required dependencies
    const requiredDeps = ['react', 'react-dom', 'react-router-dom', 'axios'];
    const missingDeps = requiredDeps.filter(dep => !packageJson.dependencies || !packageJson.dependencies[dep]);

    if (missingDeps.length > 0) {
      log(`✗ Missing dependencies: ${missingDeps.join(', ')}`, 'red');
      return false;
    }

    log(`✓ All required dependencies present in package.json`, 'green');
    return true;
  } catch (error) {
    log(`✗ Error reading package.json: ${error.message}`, 'red');
    return false;
  }
}

function checkNodeModules() {
  log('\n📚 Checking node_modules installation...', 'blue');
  try {
    const nodeModulesPath = path.join(__dirname, 'node_modules');
    if (!fs.existsSync(nodeModulesPath)) {
      log('✗ node_modules directory not found', 'red');
      log('  Run: npm install', 'yellow');
      return false;
    }

    // Check for key dependencies
    const requiredModules = [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      'vite',
      'typescript',
    ];

    const missingModules = requiredModules.filter(
      mod => !fs.existsSync(path.join(nodeModulesPath, mod))
    );

    if (missingModules.length > 0) {
      log(`✗ Missing modules: ${missingModules.join(', ')}`, 'red');
      log('  Run: npm install', 'yellow');
      return false;
    }

    log('✓ All required node_modules are installed', 'green');
    return true;
  } catch (error) {
    log(`✗ Error checking node_modules: ${error.message}`, 'red');
    return false;
  }
}

function checkTypeScriptConfig() {
  log('\n⚙️  Checking TypeScript configuration...', 'blue');
  try {
    const tsconfigPath = path.join(__dirname, 'tsconfig.json');
    if (!fs.existsSync(tsconfigPath)) {
      log('✗ tsconfig.json not found', 'red');
      return false;
    }

    const tsconfig = JSON.parse(fs.readFileSync(tsconfigPath, 'utf8'));
    log('✓ tsconfig.json found and valid', 'green');
    return true;
  } catch (error) {
    log(`✗ Error reading tsconfig.json: ${error.message}`, 'red');
    return false;
  }
}

function checkViteConfig() {
  log('\n⚡ Checking Vite configuration...', 'blue');
  try {
    const viteConfigPath = path.join(__dirname, 'vite.config.ts');
    if (!fs.existsSync(viteConfigPath)) {
      log('✗ vite.config.ts not found', 'red');
      return false;
    }

    log('✓ vite.config.ts found', 'green');
    return true;
  } catch (error) {
    log(`✗ Error checking vite.config.ts: ${error.message}`, 'red');
    return false;
  }
}

function checkSourceFiles() {
  log('\n📝 Checking source files...', 'blue');
  try {
    const requiredFiles = [
      'src/main.tsx',
      'src/App.tsx',
      'index.html',
    ];

    const missingFiles = requiredFiles.filter(
      file => !fs.existsSync(path.join(__dirname, file))
    );

    if (missingFiles.length > 0) {
      log(`✗ Missing source files: ${missingFiles.join(', ')}`, 'red');
      return false;
    }

    log('✓ All required source files present', 'green');
    return true;
  } catch (error) {
    log(`✗ Error checking source files: ${error.message}`, 'red');
    return false;
  }
}

function runTypeCheck() {
  log('\n🔍 Running TypeScript type check...', 'blue');
  try {
    execSync('npm run type-check', {
      cwd: __dirname,
      stdio: 'pipe',
    });
    log('✓ TypeScript type check passed', 'green');
    return true;
  } catch (error) {
    log('✗ TypeScript type check failed', 'red');
    log(`  ${error.message}`, 'yellow');
    return false;
  }
}

function runBuild() {
  log('\n🏗️  Running production build...', 'blue');
  try {
    execSync('npm run build', {
      cwd: __dirname,
      stdio: 'pipe',
    });

    // Check if dist directory was created
    const distPath = path.join(__dirname, 'dist');
    if (fs.existsSync(distPath)) {
      log('✓ Production build successful', 'green');
      log(`✓ Build output created in: ${distPath}`, 'green');
      return true;
    } else {
      log('✗ Build succeeded but dist directory not found', 'red');
      return false;
    }
  } catch (error) {
    log('✗ Production build failed', 'red');
    log(`  ${error.message}`, 'yellow');
    return false;
  }
}

// Main verification function
async function main() {
  log('═══════════════════════════════════════════════════', 'blue');
  log('  Frontend Installation Verification', 'blue');
  log('═══════════════════════════════════════════════════', 'blue');

  const checks = [
    { name: 'Node.js Version', fn: checkNodeVersion },
    { name: 'package.json', fn: checkPackageJson },
    { name: 'node_modules', fn: checkNodeModules },
    { name: 'TypeScript Config', fn: checkTypeScriptConfig },
    { name: 'Vite Config', fn: checkViteConfig },
    { name: 'Source Files', fn: checkSourceFiles },
    { name: 'Type Check', fn: runTypeCheck },
    { name: 'Production Build', fn: runBuild },
  ];

  const results = [];

  for (const check of checks) {
    try {
      const result = check.fn();
      results.push(result);
    } catch (error) {
      log(`\n✗ Error running ${check.name}: ${error.message}`, 'red');
      results.push(false);
    }
  }

  // Summary
  log('\n═══════════════════════════════════════════════════', 'blue');
  log('  Verification Summary', 'blue');
  log('═══════════════════════════════════════════════════', 'blue');

  const passed = results.filter(r => r).length;
  const total = results.length;

  log(`\nPassed: ${passed}/${total}`, passed === total ? 'green' : 'red');

  if (passed === total) {
    log('\n✓ All checks passed! Frontend is ready for development.', 'green');
    log('\nNext steps:', 'blue');
    log('  1. Copy .env.example to .env and configure as needed', 'yellow');
    log('  2. Start development server: npm run dev', 'yellow');
    log('  3. Visit http://localhost:5173 in your browser', 'yellow');
    process.exit(0);
  } else {
    log('\n✗ Some checks failed. Please review the errors above.', 'red');
    log('\nTroubleshooting:', 'blue');
    log('  1. Ensure Node.js 18+ is installed', 'yellow');
    log('  2. Run: npm install', 'yellow');
    log('  3. Check for error messages above', 'yellow');
    process.exit(1);
  }
}

// Run the verification
main().catch(error => {
  log(`\n✗ Fatal error: ${error.message}`, 'red');
  process.exit(1);
});

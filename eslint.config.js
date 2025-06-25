/* eslint import/no-extraneous-dependencies: 0, no-underscore-dangle: 0 */
import { FlatCompat } from '@eslint/eslintrc';
import { fileURLToPath } from 'url';
import path from 'path';
import cjsConfig from './.eslintrc.cjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

export default [
  ...compat.config(cjsConfig),
  { ignores: ['node_modules', 'public', 'dist'] },
];

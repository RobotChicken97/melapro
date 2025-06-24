/* eslint-disable import/extensions */
import { describe, it, expect } from 'vitest'
import { cn } from './utils.js'

describe('cn', () => {
  it('joins truthy class names', () => {
    expect(cn('a', null, 'b', undefined, 'c')).toBe('a b c')
  })

  it('returns empty string when all values are falsy', () => {
    expect(cn(null, undefined, false, 0, '')).toBe('')
  })
})

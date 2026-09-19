module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Allow a capitalized first letter (sentence-case), e.g. Dependabot's
    // auto-generated "Bump x from y to z" subjects. Still disallow Start Case,
    // PascalCase and UPPERCASE subjects.
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
  },
};

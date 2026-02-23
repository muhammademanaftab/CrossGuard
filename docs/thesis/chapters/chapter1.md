# Chapter 1

## 1. Introduction

### 1.1 Motivation

The web platform today has thousands of features spread across HTML, CSS, and JavaScript. Each of these features has different levels of support in different browsers. Even though browsers have become more similar over the years, there are still many differences, especially with newer features like CSS Container Queries, the `<dialog>` element, or JavaScript's `structuredClone()`. Something that works fine in Chrome might not work at all in Safari, or it might need a special vendor prefix in Firefox.

This is a big problem for web developers. They need to make sure that the code they write works correctly for all of their users, no matter which browser those users have. The usual way to deal with this is to test manually in different browsers, check the Can I Use website one feature at a time, or just rely on experience to know what is safe to use. But all of these methods take a lot of time, are easy to get wrong, and do not work well for large projects with many files.

Cross Guard was built to solve this problem through automation. Instead of checking each feature by hand, Cross Guard reads the source files, finds all the web features used in the code, and looks up each one in the Can I Use database. This way, it can find every compatibility issue in a file, a folder, or a whole project in just a few seconds, turning what used to be hours of manual work into an automatic process.

On top of that, more and more development teams are using CI/CD (Continuous Integration / Continuous Deployment) pipelines to build and deploy their code automatically. These teams need tools that can check for problems on every commit without human intervention. Just like linters check code quality and type checkers verify types, Cross Guard can check browser compatibility automatically, stopping compatibility problems from reaching production.

### 1.2 Goals

The main goal of this project is to build a tool that automatically finds browser compatibility issues in HTML, CSS, and JavaScript source files. More specifically, Cross Guard aims to:

1. **Parse web source files accurately** by using AST-based (Abstract Syntax Tree) parsing with tinycss2 for CSS, tree-sitter for JavaScript, and BeautifulSoup4 for HTML. The parsers extract the web platform features used in the code while keeping false positives to a minimum through careful filtering.

2. **Analyze compatibility** by looking up each detected feature in the Can I Use database and checking its support status in the target browsers (Chrome, Firefox, Safari, Edge). The tool then calculates a weighted compatibility score from 0 to 100 and assigns a letter grade.

3. **Provide two frontends** with a desktop GUI for interactive use and a production CLI for automated pipelines. Both share the same backend through a service facade, so the results are always the same no matter which interface is used.

4. **Work with CI/CD pipelines** by supporting standard output formats like SARIF 2.1.0 (for GitHub Code Scanning), JUnit XML (for Jenkins and GitLab CI), and Checkstyle XML (for SonarQube). It also provides quality gates that can fail a build when compatibility drops below a set threshold.

5. **Be extensible** through a custom rules system that lets users define their own feature detection patterns without changing the source code. Users can also configure which browsers and versions to target.

6. **Save analysis history** in a local SQLite database, so users can look back at past results, bookmark important analyses, and organize them with tags.

### 1.3 Scope of the Project

The scope of Cross Guard covers the following areas:

1. **Multi-Language Source Parsing**
   The tool parses three web languages (HTML, CSS, and JavaScript) using dedicated parsers. Each parser uses AST (Abstract Syntax Tree) techniques to accurately extract features from the code. The HTML parser can detect over 100 elements, attributes, and input types. The CSS parser detects over 150 properties, selectors, and at-rules. The JavaScript parser can detect 278 Can I Use feature IDs using a 3-tier strategy: AST node types, AST identifiers, and regex fallback.

2. **Compatibility Analysis Engine**
   For each detected feature, the analyzer looks it up in the Can I Use database and calculates a weighted compatibility score. Features are sorted into three categories for each target browser: supported, partially supported, or unsupported. The scoring algorithm takes into account browser importance, prefix-only support, features that are disabled by default, and partial implementations.

3. **Desktop GUI Application**
   A desktop application built with CustomTkinter that includes drag-and-drop file upload, a results dashboard with score cards, browser cards, and issue cards. It also has analysis history with bookmarks and tags, a statistics panel, and a visual editor for custom rules.

4. **Production CLI with CI/CD Integration**
   A command-line interface built with Click that supports 6 export formats (JSON, PDF, SARIF, JUnit XML, Checkstyle XML, CSV). It includes quality gates for automated builds, stdin support for piped content, `.crossguardignore` file exclusion, and CI configuration generators for GitHub Actions, GitLab CI, and pre-commit hooks.

5. **Project-Level Analysis**
   The tool can scan entire project directories recursively. It detects which frameworks are being used (React, Vue, Angular, etc.) and produces an aggregated compatibility report for the whole project.

6. **Polyfill Recommendations**
   When the tool finds unsupported features, it automatically suggests polyfills that can fix the compatibility issues. This helps developers find solutions quickly.

7. **Machine Learning Risk Prediction**
   An optional ML module built with scikit-learn that predicts compatibility risk levels based on the patterns of feature usage in the code. This gives developers a heads-up about potential problems before they become real issues.

8. **Data Persistence**
   A SQLite database with 8 tables that stores analysis history, user settings, bookmarks, and tags. The database has schema versioning and handles migrations automatically when upgrading.

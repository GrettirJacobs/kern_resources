# Frontend Repository Structure Decision

**Date:** April 7, 2025  
**Author:** Kern Resources Team

## Overview

This document outlines the decision-making process for structuring the Kern Resources frontend code in relation to the existing backend repository. We evaluated whether to create a separate repository for the frontend or to include it as a subdirectory in the existing repository.

## Options Considered

### Option 1: Separate Repository for Frontend

**Approach:** Create a new GitHub repository dedicated solely to the static website frontend.

**Advantages:**
- Clear separation of concerns between frontend and backend
- Independent versioning and release cycles
- Potentially simpler CI/CD pipelines for frontend-only changes
- Reduced repository size and clone time for frontend developers
- Ability to use different technology stacks without affecting the backend

**Disadvantages:**
- Coordination challenges when API changes affect both repositories
- More complex development environment setup (need to clone and run two repos)
- Difficulty sharing common code, types, or utilities
- Documentation spread across multiple repositories
- Additional overhead in managing multiple repositories

### Option 2: Subdirectory in Existing Repository

**Approach:** Create a subdirectory (e.g., `frontend/`) in the existing Kern Resources repository.

**Advantages:**
- Unified codebase with all project code in one place
- Simplified development workflow (single clone, single PR for related changes)
- Easier to share types, constants, and utilities between frontend and backend
- Consistent documentation in one location
- Render supports deploying from subdirectories
- Coordinated changes to API endpoints and their consumers
- Simplified project history and context

**Disadvantages:**
- Potentially larger repository size
- Risk of tight coupling between frontend and backend
- May complicate CI/CD if not configured properly
- Could become unwieldy if the project grows significantly

## Decision

**We have decided to implement Option 2: Include the frontend as a subdirectory in the existing repository.**

This decision was made based on the following factors:

1. **Project Scale:** Kern Resources is currently a hobby project with a limited number of contributors, making a monorepo approach more manageable.

2. **Development Efficiency:** Having both frontend and backend in the same repository simplifies the development workflow, especially when making changes that affect both parts.

3. **Render Support:** Render explicitly supports deploying from subdirectories in a repository, making this approach compatible with our hosting plans.

4. **Coordination Benefits:** The ability to make coordinated changes to both frontend and backend in a single pull request will reduce integration issues.

5. **Documentation Cohesion:** Keeping all documentation in one place will make it easier for future contributors to understand the entire system.

## Implementation Plan

The repository will be structured as follows:

```
kern_resources/
├── backend/                # Existing Flask application (renamed from app/)
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── ...
├── frontend/               # New static site directory
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   ├── package.json        # Frontend dependencies
│   └── README.md           # Frontend documentation
├── docs/                   # Project documentation
├── tests/                  # Test suite
└── README.md               # Main project README
```

### Deployment Configuration

When setting up the static site on Render:

1. Connect to the GitHub repository
2. Specify `frontend` as the root directory
3. Configure the build command and publish directory relative to the `frontend` directory

For example:
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Publish Directory:** `dist` or `build` (depending on the frontend framework)

## Future Considerations

If the project grows significantly in the future, we may reconsider this decision. Factors that would prompt a reevaluation include:

1. Large team with separate frontend and backend developers
2. Significant increase in repository size affecting performance
3. Need for completely independent release cycles
4. Different technology stacks requiring different CI/CD pipelines

## Conclusion

The subdirectory approach provides the best balance of simplicity, coordination, and deployment compatibility for the current scale and needs of the Kern Resources project. This structure will support our immediate goal of deploying a static frontend on Render while maintaining a cohesive codebase.

# Changelog

All notable changes to this project will be documented in this file.

## [v1.1.2] - 2025-12-28
### Added
- **Configurable Workspace**: New settings UI to change the active workspace folder directly from the application.
- **Documentation Access**: Added direct link to documentation in the header.

### Fixed
- **Workspace Configuration**: Fixed path resolution issues that caused "Workspace not configured" errors.
- **Documentation Link**: Fixed 404 error by correctly routing to the `docs` directory.
- **Port Conflict**: Improved startup reliability by handling previous instances.

## [v1.0.1] - 2025-12-28

### Added
- **Project Rename**: Officially renamed from "OmniDoc" to "**DocNexus**".
- **Bootstrap Icons**: Integration of Bootstrap Icons for consistent, high-quality SVG iconography across the application.
- **Mobile Optimization**: improved responsive design with adaptive margins and typography scaling for mobile devices.
- **Unified UI**: Standardized "glassmorphic" button styling for Edit, Export, Theme Toggle, and Top buttons.

### Changed
- **Theme Toggle**: Improved icon logic to show the *target* state (Sun icon when Dark, Moon icon when Light) for better UX.
- **Icons**: Replaced all remaining emojis with professional SVG icons.
- **Margins**: Optimized document viewing margins (15% on desktop -> 5% on mobile).

### Fixed
- **URL Cleanliness**: Removed ephemeral `?smart=false` query parameter from document URLs.
- **Smart Feature**: Removed experimental "Smart Toggle" feature code and UI elements (deferred to v1.1).
- **Navigation**: Fixed floating "Top" button icon and styling.
- **Theme Icon**: Fixed critical bug where theme toggle displayed a music note icon instead of a moon icon due to Unicode mismatch.
- **Layout Redesign**: Implemented modern, centered document layout (max-width 1000px) with fixed 32px padding, replacing inconsistent percentage-based margins.
- **Project Structure**: Renamed `doc` to `docs` (standard) and refactored sample content from `workspace` to `examples` (source) -> `workspace` (release).

## [v1.0.0] - 2025-12-28
- Initial Release

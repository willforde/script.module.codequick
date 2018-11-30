# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- 

## [0.9.7] - 2018-11-30
### Changed
- Related menu now shows "Related videos" as the category.

### Added
- Ability to get and set listitem params as attributes, e.g. item.info.size = 132156.
- Subtitles can now be added to a listitem by using the "item.subtitles" list.
- "content_type" auto selection can now be disable by setting "plugin.content_type = None".
- "plugin.add_sort_methods" now except a keyword only argument called "disable_autosort", to disable auto sorting.

### Fixed
- Watchflags now working with Kodi v18, plugin url path component required a trailing "/".
- Youtube playlist would crash when a playlist contained duplicate videos.

### Removed
- "\_\_version__" from \_\_init__.py.
- "Total Execution Time" check as it don't work right when using "reuselanguageinvoker".
- "youtube.CustomRow" class as it was not used anymore.

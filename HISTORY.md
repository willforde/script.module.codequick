# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.9.12] - 2020-06-19
### Fixed
- Attempt fix for 'import _strptime' failure.

### Changed
- Run method now returns the exception that was raise when error occurs
- 'set_callback' now excepts a path to a callback.
- No need to always import callback modules. Modules are auto loaded based on the specified path.


## [0.9.10] - 2019-05-24
### Changed
- Improved error handling
- Delayed callbacks can now be set to run only when there are no errors, or only when there are errors, or run regardless of errors or not.
- Delayed callbacks can now access the exception that was raised by setting an argument name to exception.

### Added
- Added support to auto redirect to the first listitem if there is only one single listitem

## [0.9.9] - 2019-04-25
### Added
- Allow to disable automatic setting of fanart, thumbnail or icon images.
- Allow for plugin paths as folders in set_callback.
- Allow for a callback path to be passed instead of a function

## [0.9.8] - 2019-03-11
### Fixed
- Dailymotion videos not working when using extract_source.

## [0.9.7] - 2018-11-30
### Changed
- Related menu now shows "Related videos" as the category.

### Added
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

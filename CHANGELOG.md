Changelog
=========

0.4.0

- Add Windows support. Thanks berdon (https://github.com/berdon)

0.3.9

- Fix issue where add with force would only remove entries matching the first name in the new entry. Thanks graemerobertson (https://github.com/graemerobertson)

0.3.8

- Fix TypeError in 'remove_all_matching()' if empty lines found. Thanks stardust85 (https://github.com/stardust85) 

0.3.7

- Enable force option for import_url

0.3.6

- Fix regressions that meant comments were stripped and example imports failed.

0.3.5

- Fix bug in 'remove_all_matching()' where comments exist in hosts entries.

0.3.4

- Fix 'remove_all_matching()'. Thanks dmtucker (https://github.com/dmtucker)
- Add option to write hosts files to an alternative path
- Increase test coverage and the number of python versions tested against

0.3.3

- Fix issue in `remove_all_matching()` which could cause entries to be skipped

0.3.1

- Add repr and str for each class
- Fix python 3 incompatibility issue

0.3.0

- Various refactoring to simplify and make code more readable/pythonic
- Get coverage back to 100%
- Add documentation to Read The Docs
- Various PEP8 improvements

0.2.12

- Minor bug fixes

0.2.11

- Minor bug fixes

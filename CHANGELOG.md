Changelog
=========

1.0.1

- Add function to enable finding host entries by name or address

1.0.0

- Promote to 1.0.0 now it is being used in production
- Add support for Python 3.8
- Remove support for Python 3.4 due to dependency PyYAML [dropping support](https://github.com/yaml/pyyaml/issues/281)

0.4.6

- Enable merging of entries
- Remove unnecessary win_inet_pton requirement. Thanks dotlambda (https://github.com/dotlambda)
- Support adding comments

0.4.5

- Add win_inet_pton to requirements

0.4.4

- Linting

0.4.3

- Freeze win_inet_pton version

0.4.2

- Travis build changes

0.4.1

- Add option to allow duplicate IPs. Thanks Konstantin (https://github.com/Koc)
- Update test integration

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

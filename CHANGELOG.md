# Changelog

## v0.4.0 - 2024-09-02

* Updated `fica.Key` to assume that `factory` returns a value of the correct type if `type_` is specified per [#33](https://github.com/chrispyles/fica/issues/33)
* Added the `required` argument to `fica.Key` per [#13](https://github.com/chrispyles/fica/issues/13)
* Update `fica.Config` to support inheritance per [#35](https://github.com/chrispyles/fica/issues/35)

## v0.3.1 - 2023-08-20

* Updated `fica.Config` to mark a key as not-defaulted when it is updated using `__setattr__`

## v0.3.0 - 2023-08-20

* Added the `factory` argument to `fica.Key` per [#21](https://github.com/chrispyles/fica/issues/21)
* Added user config key validation to `fica.Config` per [#12](https://github.com/chrispyles/fica/issues/12)
* Added `fica.Key.get_default` per [#17](https://github.com/chrispyles/fica/issues/17)
* Updated Sphinx extension to always show subkeys for keys with subkey containers and to show the default value in a comment at the top of the subkeys per [#25](https://github.com/chrispyles/fica/issues/25)
* Clarified error messages for errors thrown when creating/updating `fica.Config` objects per [#29](https://github.com/chrispyles/fica/issues/29)

## v0.2.2 - 2022-10-31

* Added `MANIFEST.in`

## v0.2.1 - 2022-10-31

* Fixed the repo URL in `setup.py`

## v0.2.0 - 2022-07-16

* Added the `name` argument to `fica.Key`
* Added `fica.Config.get_user_config` per [#19](https://github.com/chrispyles/fica/issues/19)
* Renamed `fica.Config.update_` to `fica.Config.update`

## v0.1.1 - 2022-07-05

* Fixed `fica.Config` to maintain the order keys are declared in
* Added the `documentation_mode` argument to `fica.Config`

## v0.1.0 - 2022-06-25

* Convert to object-oriented model of configuration definition
* Added validation tools for user-specified values for keys per [#5](https://github.com/chrispyles/fica/issues/5)

## v0.0.1 - 2022-04-17

* Initial release

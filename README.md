# Rustix

Generates nix derivations from a `Cargo.lock` file, which use `mkRustCrate` from @P-E-Meunier. It will create one derivation for the project and one for each included dependency, with version and hashes from the lockfile (similar to @P-E-Meunier's).

State: Very much incomplete, only basic applications will work.

Key points
- Only uses a single `Cargo.lock` file as input, does not fetch anything
- Does not need a registry (all information is included in the lockfile)
- Builds each dependency separately so they can be shared between applications (if they have the same version inside the lockfile)
- shas of git dependencies need to be specified separately (not included in the lockfile)

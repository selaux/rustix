import argparse
import os.path as path
import pytoml as toml

def nix_derivation_name(name, version):
    return "{}_{}".format(name.replace("-", "_"), version.replace('.', '_'))

def build_metadata_key(package):
    return "checksum {} {} ({})".format(package['name'], package['version'], package['source'])

def dependency_to_derivation_name(dependency):
    [ name, version ]  = dependency.split(' ')[:2]
    return nix_derivation_name(name, version)

def make_package_derivation(metadata, package):
    name = package['name']
    version = package['version']
    dependencies = [ dependency_to_derivation_name(d) for d in package['dependencies'] ] if 'dependencies' in package else None
    dependencies_string = "dependencies = [ {} ];".format(' '.join(dependencies)) if dependencies else ""
    derivation = {
        'name': name,
        'version': version,
        'derivation_name': nix_derivation_name(name, version),
        'dependencies': dependencies_string, 
        'sha256': metadata[build_metadata_key(package)], 
    }
    
    return """{derivation_name} = mkRustCrate {{
        crateName = "{name}";
        version = "{version}";
        {dependencies}
        src = fetchurl {{
            url = "https://crates.io/api/v1/crates/{name}/{version}/download";
            sha256 = "{sha256}";
            name = "{name}-{version}.tar.gz";
        }};
        inherit release;
    }};""".format(**derivation)

argparser = argparse.ArgumentParser(description='Build nix derivations from Cargo.lock')
argparser.add_argument('lockfile', help='Path to Cargo.lock')

args = argparser.parse_args()

with open(path.realpath(args.lockfile), 'rb') as lf:
    lockfile = toml.load(lf)

    root = lockfile['root']
    root['dependencies'] = ' '.join([ dependency_to_derivation_name(d) for d in root['dependencies'] ])

    dep_derivations = '\n'.join([ make_package_derivation(lockfile['metadata'], package) for package in lockfile['package'] ])
    top_level_derivation = """
        {{ mkRustCrate, fetchurl }}:
        let
            release = true;
            {other_derivations}
        in
        mkRustCrate {{
            crateName = "{root[name]}";
            version = "{root[version]}";
            dependencies = [ {root[dependencies]} ];
            src = ./.;
            inherit release;
        }}
    """.format(**{
        'other_derivations': dep_derivations,
        'root': root
    })
    print(top_level_derivation)


#!/usr/bin/env python

import argparse
import os.path as path
import pytoml as toml
import textwrap


def derivation_name(name, version):
    return "{}_{}".format(name.replace("-", "__"), version.replace('.', '_'))


def dedent(str):
    return textwrap.dedent(str).strip()


class CrateDerivation:
    def __init__(self, package):
        self.name = package['name']
        self.version = package['version']
        self.source = package['source'] if 'source' in package else None
        self.dependencies = package.get('dependencies', [])
        self.sha256 = package['sha256'] if 'sha256' in package else None

    def derivation_name(self):
        return derivation_name(self.name, self.version)

    def render_src(self):
        raise NotImplementedException('Render called for dependency with unknown type: {}', self.name)

    def render_dependencies(self):
        return "dependencies = [ {} ];".format(' '.join([
            derivation_name(*d.split(' ')[:2]) for d in self.dependencies
        ]))

    def render(self):
        return dedent("""
            {derivation_name} = mkRustCrate {{
                crateName = "{name}";
                version = "{version}";
                {dependencies}
                {src}
                inherit release;
            }};
        """).format(**{
            'name': self.name,
            'derivation_name': self.derivation_name(),
            'version': self.version,
            'dependencies': self.render_dependencies() if len(self.dependencies) > 0 else '',
            'src': textwrap.indent(self.render_src(), '    ')
        })


class RootCrateDerivation(CrateDerivation):
    def render_src(self):
        return 'src = ./.;'


class VersionedCrateDerivation(CrateDerivation):
    def render_src(self):
        return dedent("""
            src = fetchurl {{
                url = "https://crates.io/api/v1/crates/{name}/{version}/download";
                sha256 = "{sha256}";
                name = "{name}-{version}.tar.gz";
            }};
        """).format(name=self.name, version=self.version, sha256=self.sha256)


class GitCrateDerivation(CrateDerivation):
    def render_src(self):
        [ url, rev ] = self.source.split('#')

        return dedent("""
            src = fetchgit {{
                url = "{url}";
                rev = "{rev}";
                sha256 = "{sha256}";
            }};
        """).format(url=url[4:], rev=rev, sha256=self.sha256)


def metadata_key(package):
    source = package['source'].split('#')[0] if package['source'].startswith('git+') else package['source']
    return "checksum {} {} ({})".format(package['name'], package['version'], source)


def dependency_derivation(package, metadata):
    sha256 = metadata[metadata_key(package)]
    if package['source'].startswith('git+'):
        return GitCrateDerivation({ **package ,'sha256': sha256})
    return VersionedCrateDerivation({ **package ,'sha256': sha256})


def render_nix_from_cargo_lock(lockfile, additional_checksums):
    metadata = {**lockfile['metadata'], **{"checksum " + name: val for name, val in additional_checksums.items()}}

    root = RootCrateDerivation(lockfile['root'])
    dependeny_derivations = [dependency_derivation(package, metadata) for package in lockfile['package']]
    all_derivations_rendered = [d.render() for d in dependeny_derivations] + [ root.render() ]

    return dedent("""
        {{ mkRustCrate, fetchurl, fetchgit }}:
        let
            release = true;
        {derivations}
        in
            {root}
    """).format(**{
        'derivations': '\n'.join([ textwrap.indent(d, '    ') for d in all_derivations_rendered ]),
        'root': root.derivation_name()
    })


argparser = argparse.ArgumentParser(description='Build nix derivations from Cargo.lock')
argparser.add_argument('crate', help='Path to crate (where Cargo.toml and Cargo.lock are located')
argparser.add_argument('--additional-checksum', nargs=2, action='append', help='Define additional checksums, e.g. for git repositories')

args = argparser.parse_args()

with open(path.realpath(path.join(args.crate, 'Cargo.lock')), 'rb') as lf:
    lockfile = toml.load(lf)
    rendered = render_nix_from_cargo_lock(lockfile, dict(args.additional_checksum or []))
    print(rendered)


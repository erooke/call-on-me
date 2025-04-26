{
  system ? builtins.currentSystem,
  pins ? import ./nix/npins,
  pkgs ? import pins.nixpkgs { inherit system; },
}:
let
  python = pkgs.python3.withPackages (ps: [
    ps.jinja2
    ps.arrow
    ps.lxml
    ps.ical
    ps.requests
    ps.pillow
  ]);
in
pkgs.mkShell {
  nativeBuildInputs = [
    python
    pkgs.fswatch
    pkgs.npins
    pkgs.ruff
  ];
}

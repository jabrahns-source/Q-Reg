# Contributing to Q-REG

Thank you for considering contributing to Q-REG.

## Development Process
1. Fork the repo
2. Create a feature branch
3. Make changes + run formal verification (`cd formal && make check`)
4. Ensure all Idris theorems hold and Rust tests pass
5. Submit a Pull Request

## Code Standards
- Idris code must be total and pass totality checker
- Rust code must be zero-cost where possible
- All compliance rules must maintain mathematical guarantees

Questions? Open an issue.
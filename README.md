# Simio Portal REST API with pySimio

This repository demonstrates how to programmatically run Simio model experiments on Simio Portal using the REST API through the `pySimio` Python library.

## Overview

The repository contains examples showing how to interact with Simio Portal to execute simulation experiments remotely. This approach is useful for automation, batch processing, integration with other systems, or running experiments from environments where the Simio desktop application is not available.

## Repository Contents

### Python Scripts
- **`Experiment Runner.ipynb`** - Jupyter notebook with interactive examples and detailed explanations
- **`create_run.py`** - Standalone Python script for running experiments
- **`helper.py`** - Helper functions and utilities

### Simio Models
- **`Optimization Example 03.spfx`** - Model with `Generate Statistics` set to `False` for faster execution
- **`Optimization Example 03 Stats.spfx`** - Model with `Generate Statistics` set to `True` to generate Pivot Grid statistics

### Configuration Files
- **`requirements.txt`** - Python package dependencies
- **`sample.env`** - Template for environment variables (credentials and configuration)

The key difference between the two models is the `Generate Statistics` experiment property:
- **Without statistics** (`Optimization Example 03`): Runs faster and still produces experiment response outputs
- **With statistics** (`Optimization Example 03 Stats`): Generates full Pivot Grid statistics for detailed analysis

## Prerequisites

- Python 3.7 or higher
- Active Simio Portal account with API access
- `pySimio` library
- `jupyter` (for running the notebook)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/jsmithSimio/SimioPortalScripting.git
cd SimioPortalScripting
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Configure your credentials:
   - Copy `sample.env` to `.env`
   - Edit `.env` with your Simio Portal credentials and settings

## Usage

### Option 1: Jupyter Notebook (Recommended for Learning)

1. Launch Jupyter:
```bash
jupyter notebook
```

2. Open `Experiment Runner.ipynb` and follow the step-by-step instructions

### Option 2: Standalone Python Script

1. Ensure your `.env` file is configured with credentials
2. Run the script:
```bash
python create_run.py
```

## Key Features Demonstrated

- **Authentication**: Connecting to Simio Portal using API credentials
- **Model Upload**: Uploading Simio model files to Portal
- **Experiment Execution**: Running experiments with custom parameters
- **Results Retrieval**: Downloading and parsing experiment results
- **Error Handling**: Managing common API errors and timeouts

## pySimio Library

This repository uses the `pySimio` library, which provides a Python interface to the Simio Portal REST API. Key capabilities include:

- Simple authentication and session management
- Easy model and experiment manipulation
- Automatic handling of async operations
- Results parsing and data extraction

For more information about pySimio, visit: [pySimio Documentation](https://pypi.org/project/pySimio/)

## Model Details

The included models demonstrate a typical optimization scenario. The choice between models depends on your needs:

- Use **Optimization Example 03** when you only need response outputs and want faster execution
- Use **Optimization Example 03 Stats** when you need detailed statistics and Pivot Grid data for analysis

## Configuration

Before running the examples, configure your `.env` file (copied from `sample.env`) with:

1. **Portal Credentials**: Your Simio Portal username and API key
2. **Project Information**: Your Portal project ID or name
3. **Model Settings**: Experiment name and any input parameters

The `.env` file keeps your credentials secure and separate from the code.

## Common Use Cases

- **Automated Testing**: Run experiments automatically as part of a CI/CD pipeline
- **Parameter Sweeps**: Systematically explore parameter spaces
- **Integration**: Connect Simio simulations with other business systems
- **Batch Processing**: Run multiple experiments unattended
- **Remote Execution**: Run simulations without the desktop application

## Troubleshooting

### Authentication Issues
- Verify your API credentials are correct
- Check that your Portal account has API access enabled

### Upload Failures
- Ensure model files are not corrupted
- Check file size limits for your Portal account

### Experiment Timeouts
- Consider using the faster model (without statistics) for long experiments
- Increase timeout values in the script if needed

## Best Practices

- **Model Selection**: Use the non-statistics model for production runs where only response data is needed
- **Error Handling**: Always implement proper error handling for production code
- **Credentials**: Never commit API credentials to version control
- **Timeouts**: Set appropriate timeouts based on expected experiment duration

## Additional Resources

- [Simio Portal Documentation](https://www.simio.com/resources/simio-portal/)
- [Simio API Reference](https://www.simio.com/api/)
- [pySimio GitHub Repository](https://github.com/SimioLLC/pySimio)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues related to:
- **This repository**: Open an issue on GitHub
- **pySimio library**: Contact the pySimio maintainers
- **Simio Portal**: Contact Simio support at support@simio.com

## Acknowledgments

- Simio LLC for providing the Portal API and pySimio library
- The example models are based on standard Simio optimization examples

# MDPH405-ROMP-Sandbox

Interactive Python sandbox for MDPH405 Radiation Oncology Medical Physics. Students can play with voxel models, dose calculations (convolution/superposition, Monte Carlo, etc.), inverse planning, optimization, and interactive GUIs/sliders to explore compounded concepts in radiation therapy.

### Philosophy of this Sandbox

This repository is **deliberately not** a full treatment planning system.  
The goal is the opposite of clinical black-box systems like RayStation, Monaco, MOSAIQ or ARIA — which take years to master and still surprise you regularly.

Instead, we want students to **get under the hood** and freely experiment with individual concepts as they appear in lectures: voxel grids, simple dose deposition, convolution/superposition, basic Monte Carlo steps, cost functions, inverse planning, etc.

Small, transparent, modular pieces you can poke, break, and modify.

### Recommended Lightweight Open-Source Tools

These are modular, Python-first projects that let you explore individual concepts without the complexity of full clinical systems.

| Tool          | Language | Description & Strengths                                      | GitHub / Link |
|---------------|----------|-------------------------------------------------------------|---------------|
| **PortPy**    | Python   | Excellent for beamlet math, cost functions, inverse planning and optimisation playgrounds. Very educational. | [PortPy-Project/PortPy](https://github.com/PortPy-Project/PortPy) |
| **PyMedPhys** | Python   | Great utility library — DICOM handling, data conversion, QA tools, and building blocks. The perfect "glue" library. | [pymedphys/pymedphys](https://github.com/pymedphys/pymedphys) |
| **OpenTPS**   | Python   | Modular treatment planning system with good Monte Carlo support. You can use just the parts you need. | [OpenTPS on GitLab](https://gitlab.com/openmcsquare/opentps) |

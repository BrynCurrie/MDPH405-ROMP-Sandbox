# MDPH405-ROMP-Sandbox

Interactive Python sandbox for MDPH405 Radiation Oncology Medical Physics. Students can play with voxel models, dose calculations (convolution/superposition, Monte Carlo, etc.), inverse planning, optimization, and interactive GUIs/sliders to explore compounded concepts in radiation therapy.

### Philosophy of this Sandbox

This repository is **deliberately not** a full treatment planning system.  
The goal is the opposite of clinical black-box systems like RayStation, Monaco, MOSAIQ or ARIA — which take years to master and still surprise you regularly.

Instead, we want students to **get under the hood** and freely experiment with individual concepts as they appear in lectures: voxel grids, simple dose deposition, convolution/superposition, basic Monte Carlo steps, cost functions, inverse planning, etc.

Small, transparent, modular pieces you can poke, break, and modify.

### Existing Open-Source Projects in ROMP

| Project      | Language                  | Strengths                                                                 | Best For Your Sandbox                                      |
|--------------|---------------------------|---------------------------------------------------------------------------|------------------------------------------------------------|
| **PortPy**   | Python                    | Optimization algorithms, benchmark patient data from Eclipse...          | Inverse planning playgrounds, cost functions...           |
| **PyMedPhys**| Python                    | Broad library for medical physics tasks, DICOM handling, QA tools        | Utilities, data import/export...                           |
| **OpenTPS**  | Python                    | Full treatment planning system, Monte Carlo support...                   | Complete dose calculation engines...                       |
| **pyRadPlan**| Python                    | Dose calculation + optimization...                                       | Convolution/superposition...                               |
# Installation Note: D3D Desktop Duplication on Laptops

Windows has a little quirk when running Desktop Duplication on laptops with hybrid GPU systems (integrated + dedicated). You will need to perform an additional tweak to get _D3D Desktop Duplication_ to work correctly on your system.

## Problem

The problem is fully documented in [this article](https://support.microsoft.com/en-us/help/3019314/error-generated-when-desktop-duplication-api-capable-application-is-ru)

## Solution

The solution is presented as such:

> Run the application on the integrated GPU instead of on the discrete GPU

Therefore, to be able to use _D3D Desktop Duplication_ on hybrid GPU laptops, we need to force Python to run on the integrated GPU.

## Approach 1: Windows 10 Settings

_You must be running Windows 10 1809 or later for this to work._

1. Press the Windows Key, type `Graphics settings` and press enter
2. You should see the following window:  
![image](https://user-images.githubusercontent.com/35039/84433008-a3b65d00-abfb-11ea-8343-81b8f265afc4.png)
3. Make sure the dropdown is set to `Desktop App` and click `Browse`
4. Find the `python.exe` used by your _D3D Desktop Duplication_ project. Example:  
![image](https://user-images.githubusercontent.com/35039/84433419-3d7e0a00-abfc-11ea-99a4-b5176535b0e5.png)
5. Click on `Options`
6. Select `Power saving` and click `Save`  
![image](https://user-images.githubusercontent.com/35039/84433562-7918d400-abfc-11ea-807a-e3c0b15d9fb2.png)
7. If you did everything right it should look like this:  
![image](https://user-images.githubusercontent.com/35039/84433706-bda46f80-abfc-11ea-9c64-a702b96095b8.png)
8. Repeat the process for other potentially relevant executables for your project: `ipython.exe`, `jupyter-kernel.exe` etc.

## Approach 2: Nvidia Control Panel

Need help to fill in this section. See issue [SerpentAI/D3DShot#27](https://github.com/SerpentAI/D3DShot/issues/27)

## Approach 3: AMD Catalyst Control Center

Need help to fill in this section. See issue [SerpentAI/D3DShot#28](https://github.com/SerpentAI/D3DShot/issues/28)

## Question: Won't this impede on my ability to use CUDA, OpenCL etc?

Preliminary answer: No. This is telling Windows how to _render_ Python processes with the Desktop Window Manager. Most Python applications are console applications that don't have a window. Even if you have a GUI application with one or more windows, this should only affect the rendering aspect (i.e. your windows won't be rendered through the dedicated GPU) and shouldn't limit hardware access in any way.

---
(copied and adapted from <https://github.com/SerpentAI/D3DShot/wiki/Installation-Note:-Laptops>)

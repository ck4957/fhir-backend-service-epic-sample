; ObjectScript installer for IRIS
; Run this from the IRIS terminal to set up the RevStream namespace and classes

Class RevStream.Installer
{

/// Main installation method
ClassMethod Install() As %Status
{
    Set tStatus = $$$OK
    
    Try {
        Write "Installing RevStream Integration Pipeline...", !
        
        // Create directories
        Set tStatus = ..CreateDirectories()
        If $$$ISERR(tStatus) Quit
        
        // Compile all classes
        Set tStatus = ..CompileClasses()
        If $$$ISERR(tStatus) Quit
        
        // Create the production
        Set tStatus = ..SetupProduction()
        If $$$ISERR(tStatus) Quit
        
        Write !, "Installation complete!", !
        Write "Start the production from: Interoperability > Configure > Production", !
        
    } Catch ex {
        Set tStatus = ex.AsStatus()
        Write "Installation failed: ", $System.Status.GetErrorText(tStatus), !
    }
    
    Quit tStatus
}

/// Create required directories
ClassMethod CreateDirectories() As %Status
{
    Set tStatus = $$$OK
    
    Write "Creating directories...", !
    
    // Create error directory
    Set tDir = "/home/irisowner/errors/"
    If '##class(%File).DirectoryExists(tDir) {
        Set tCreated = ##class(%File).CreateDirectory(tDir)
        If 'tCreated {
            Write "  Warning: Could not create ", tDir, !
        } Else {
            Write "  Created: ", tDir, !
        }
    }
    
    Quit tStatus
}

/// Compile all RevStream classes
ClassMethod CompileClasses() As %Status
{
    Set tStatus = $$$OK
    
    Write "Compiling classes...", !
    
    Set tStatus = $System.OBJ.CompilePackage("RevStream", "ck")
    
    If $$$ISOK(tStatus) {
        Write "  Classes compiled successfully", !
    } Else {
        Write "  Warning: Some classes may have compilation errors", !
    }
    
    Quit tStatus
}

/// Set up the production
ClassMethod SetupProduction() As %Status
{
    Set tStatus = $$$OK
    
    Write "Setting up production...", !
    
    // The production is defined in RevStream.Production.RevStreamProduction
    Write "  Production ready: RevStream.Production.RevStreamProduction", !
    
    Quit tStatus
}

}

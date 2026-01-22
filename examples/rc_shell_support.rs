// rc_shell_support.rs
// Example Rust code showing how to add rc shell support to tools like aichat
//
// This file demonstrates the minimal changes needed to add Plan 9 rc shell
// support to AI chat tools. It follows the same patterns used in sigoden/aichat.
//
// To compile this example, add to your Cargo.toml:
// [dependencies]
// dirs = "5.0"

use std::{
    env,
    fs::OpenOptions,
    io::{self, Write},
    path::{Path, PathBuf},
};

/// Shell configuration
pub struct Shell {
    pub name: String,
    pub cmd: String,
    pub arg: String,
}

impl Shell {
    pub fn new(name: &str, cmd: &str, arg: &str) -> Self {
        Self {
            name: name.to_string(),
            cmd: cmd.to_string(),
            arg: arg.to_string(),
        }
    }
}

/// Detect the current shell, including rc shell support
pub fn detect_shell() -> Shell {
    let cmd = env::var("SHELL").ok().or_else(|| {
        if cfg!(windows) {
            // Windows shell detection
            if let Ok(ps_module_path) = env::var("PSModulePath") {
                let ps_module_path = ps_module_path.to_lowercase();
                if ps_module_path.starts_with(r"c:\users") {
                    if ps_module_path.contains(r"\powershell\7\") {
                        return Some("pwsh.exe".to_string());
                    } else {
                        return Some("powershell.exe".to_string());
                    }
                }
            }
            None
        } else {
            None
        }
    });
    
    let name = cmd
        .as_ref()
        .and_then(|v| Path::new(v).file_stem().and_then(|v| v.to_str()))
        .map(|v| {
            if v == "nu" {
                "nushell".into()
            } else {
                v.to_lowercase()
            }
        });
    
    let (cmd, name) = match (cmd.as_deref(), name.as_deref()) {
        (Some(cmd), Some(name)) => (cmd, name),
        _ => {
            if cfg!(windows) {
                ("cmd.exe", "cmd")
            } else {
                ("/bin/sh", "sh")
            }
        }
    };
    
    let shell_arg = match name {
        "powershell" | "pwsh" => "-Command",
        "cmd" => "/C",
        // rc shell uses -c just like most Unix shells
        "rc" | "bash" | "zsh" | "fish" | "sh" => "-c",
        _ => "-c",
    };
    
    Shell::new(name, cmd, shell_arg)
}

/// Get the history file path for a given shell, including rc shell support
pub fn get_history_file(shell: &str) -> Option<PathBuf> {
    // Note: This function uses the dirs crate for home directory detection
    // Add to Cargo.toml: dirs = "5.0"
    let home_dir = || dirs::home_dir();
    
    match shell {
        // rc shell support - check $history variable or use default
        "rc" => {
            env::var("history")
                .ok()
                .map(PathBuf::from)
                .or_else(|| Some(home_dir()?.join(".rc_history")))
        }
        "bash" | "sh" => {
            env::var("HISTFILE")
                .ok()
                .map(PathBuf::from)
                .or_else(|| Some(home_dir()?.join(".bash_history")))
        }
        "zsh" => {
            env::var("HISTFILE")
                .ok()
                .map(PathBuf::from)
                .or_else(|| Some(home_dir()?.join(".zsh_history")))
        }
        "nushell" => Some(dirs::config_dir()?.join("nushell").join("history.txt")),
        "fish" => Some(
            home_dir()?
                .join(".local")
                .join("share")
                .join("fish")
                .join("fish_history"),
        ),
        "powershell" | "pwsh" => {
            #[cfg(not(windows))]
            {
                Some(
                    home_dir()?
                        .join(".local")
                        .join("share")
                        .join("powershell")
                        .join("PSReadLine")
                        .join("ConsoleHost_history.txt"),
                )
            }
            #[cfg(windows)]
            {
                Some(
                    dirs::data_dir()?
                        .join("Microsoft")
                        .join("Windows")
                        .join("PowerShell")
                        .join("PSReadLine")
                        .join("ConsoleHost_history.txt"),
                )
            }
        }
        "ksh" => Some(home_dir()?.join(".ksh_history")),
        "tcsh" => Some(home_dir()?.join(".history")),
        _ => None,
    }
}

/// Append a command to the shell history, including rc shell support
pub fn append_to_shell_history(shell: &str, command: &str, exit_code: i32) -> io::Result<()> {
    if let Some(history_file) = get_history_file(shell) {
        let command = command.replace('\n', " ");
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64;
        
        let history_txt = match shell {
            // rc shell: simple format, just append the command
            "rc" | "bash" | "sh" => command,
            "fish" => {
                format!("- cmd: {}\n  when: {}", command, now)
            }
            "zsh" => {
                format!(": {}:{};{}", now, exit_code, command)
            }
            _ => command,
        };
        
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&history_file)?;
        writeln!(file, "{}", history_txt)?;
    }
    Ok(())
}

// Example usage:
//
// fn main() {
//     let shell = detect_shell();
//     println!("Detected shell: {}", shell.name);
//     println!("Shell command: {}", shell.cmd);
//     println!("Shell argument: {}", shell.arg);
//     
//     if let Some(history) = get_history_file(&shell.name) {
//         println!("History file: {}", history.display());
//     }
//     
//     // After executing a command
//     let command = "echo hello world";
//     let exit_code = 0;
//     append_to_shell_history(&shell.name, command, exit_code)
//         .expect("Failed to append to history");
// }

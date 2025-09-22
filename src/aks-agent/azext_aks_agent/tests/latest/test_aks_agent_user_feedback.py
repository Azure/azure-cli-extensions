# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_aks_agent.agent.user_feedback import ProgressReporter


class TestProgressReporter(unittest.TestCase):
    """Test cases for ProgressReporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_console = Mock()
        
    def test_show_download_progress_with_console(self):
        """Test download progress reporting with provided console."""
        # Test normal progress
        with patch('sys.stdout.isatty', return_value=True):
            ProgressReporter.show_download_progress(
                downloaded=500, 
                total=1000, 
                filename="test.bin",
                console=self.mock_console
            )
        
        self.mock_console.print.assert_called_once()
        call_args = self.mock_console.print.call_args[0][0]
        self.assertIn("Downloading test.bin", call_args)
        self.assertIn("50.0%", call_args)
        
    def test_show_download_progress_completion(self):
        """Test download progress at completion."""
        with patch('sys.stdout.isatty', return_value=True):
            ProgressReporter.show_download_progress(
                downloaded=1000,
                total=1000,
                filename="complete.bin", 
                console=self.mock_console
            )
            
        # Should be called twice - once for progress, once for newline
        self.assertEqual(self.mock_console.print.call_count, 2)
        
    def test_show_download_progress_zero_total(self):
        """Test download progress with zero total bytes."""
        ProgressReporter.show_download_progress(
            downloaded=100,
            total=0,
            filename="zero.bin",
            console=self.mock_console
        )
        
        # Should not call console when total is 0
        self.mock_console.print.assert_not_called()
        
    def test_show_download_progress_no_tty(self):
        """Test download progress when not in interactive terminal."""
        with patch('sys.stdout.isatty', return_value=False):
            ProgressReporter.show_download_progress(
                downloaded=500,
                total=1000,
                filename="notty.bin",
                console=self.mock_console
            )
            
        # Should not call console when not TTY
        self.mock_console.print.assert_not_called()
        
    
        
    def test_show_status_message_all_levels(self):
        """Test status messages with different levels."""
        test_cases = [
            ("info", "[cyan]Test info[/cyan]"),
            ("warning", "[yellow]Test warning[/yellow]"),
            ("error", "[red]Test error[/red]"),
            ("success", "[green]Test success[/green]"),
            ("unknown", "[cyan]Test unknown[/cyan]"),  # Should default to info style
        ]
        
        for level, expected_style in test_cases:
            with self.subTest(level=level):
                self.mock_console.reset_mock()
                ProgressReporter.show_status_message(
                    f"Test {level}",
                    level=level,
                    console=self.mock_console
                )
                
                self.mock_console.print.assert_called_once_with(expected_style)
                
    
        
    def test_show_binary_setup_status(self):
        """Test binary setup status message."""
        ProgressReporter.show_binary_setup_status(
            "Binary downloaded successfully", 
            console=self.mock_console
        )
        
        self.mock_console.print.assert_called_once_with(
            "[cyan]MCP Binary: Binary downloaded successfully[/cyan]"
        )
        
    def test_show_server_status(self):
        """Test server status message."""
        ProgressReporter.show_server_status(
            "Server started on port 8003",
            console=self.mock_console
        )
        
        self.mock_console.print.assert_called_once_with(
            "[cyan]MCP Server: Server started on port 8003[/cyan]"
        )
        
    def test_show_server_status_silent_mode(self):
        """Test server status in silent mode."""
        ProgressReporter.show_server_status(
            "Server status",
            silent_mode=True,
            console=self.mock_console
        )
        
        # Currently still shows in silent mode - behavior may change in future
        self.mock_console.print.assert_called_once()
        
    def test_progress_bar_formatting(self):
        """Test progress bar formatting at various percentages."""
        test_cases = [
            (0, 1000, 0),      # 0%
            (250, 1000, 25),   # 25% 
            (500, 1000, 50),   # 50%
            (750, 1000, 75),   # 75%
            (1000, 1000, 100), # 100%
            (1200, 1000, 100), # Over 100% (clamped)
        ]
        
        for downloaded, total, expected_percentage in test_cases:
            with self.subTest(downloaded=downloaded, total=total):
                self.mock_console.reset_mock()
                
                with patch('sys.stdout.isatty', return_value=True):
                    ProgressReporter.show_download_progress(
                        downloaded=downloaded,
                        total=total,
                        filename="test.bin",
                        console=self.mock_console
                    )
                    
                # For 100%, there are two calls - progress line and newline
                if expected_percentage == 100:
                    self.assertEqual(self.mock_console.print.call_count, 2)
                    # First call is the progress line
                    call_args = self.mock_console.print.call_args_list[0][0][0]
                else:
                    self.assertEqual(self.mock_console.print.call_count, 1)
                    call_args = self.mock_console.print.call_args[0][0]
                
                self.assertIn(f"{expected_percentage}.0%", call_args)
                
                # Check that progress bar contains appropriate characters
                if expected_percentage > 0:
                    self.assertIn("█", call_args)  # Filled portion should exist if > 0%
                if expected_percentage < 100:
                    self.assertIn("░", call_args)  # Empty portion should exist if < 100%


if __name__ == '__main__':
    unittest.main()

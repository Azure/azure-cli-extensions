# Azure CLI Interactive Mode

## The interactive mode for Microsoft Azure CLI (Command Line Interface)

- Interactive Tutorials
- Lightweight Drop Down Completions 
- Auto Cached Suggestions 
- Dynamic parameter completion 
- Defaulting scopes of commands
- On the fly descriptions of the commands AND parameters 
- On the fly examples of how to utilize each command 
- Query the previous command
- Navigation of example pane 
- Optional layout configurations 
- Optional "az" component 
- Fun Colors 

![Overview](docs/shell.gif)


## Updates

Azure CLI Shell is now Azure CLI Interactive Mode. To get updates, install the newest version of the CLI! First, uninstall the deprecated shell applications with:

```bash
   $ pip uninstall azure-cli-shell
```

## Running

To start the application

```bash
   $ az interactive
```

Then type your commands and hit [Enter]

To use commands outside the application

```bash
   $ #[command]
```

To Search through the last command as json
jmespath format for querying

```bash
   $ ? [param]
```

*Note: Only if the previous command dumps out json, e.g. vm list*

To only see the commands for a command

```bash
   $ %% [top-level command] [sub-level command] etc
```

To undefault a value

```bash
   $ %% ..
```

## Use Examples

Type a command, for example:

```bash
   $ vm create
```

Look at the examples

*Scroll through the pane with Control Y for up and Control N for down #*

Pick the example you want with:

```bash
   $ vm create :: [Example Number]
```

## Clear History

```bash
   $ clear-history
```

Only clears the appended suggestion when you restart the interactive shell


## Clear Screen

```bash
   $ clear
```


## Change colors

```bash
   $ az interactive --styles [option]
```

The color option will be saved.

## Cli Recommendation(Preview)
2023.04.04
####  **[Breaking Change]** Integrate the cli recommendation to make the completion ability more intelligent and provide the scenario completion.

How to enable or disable the cli recommendation
```bash
$ az config set interactive.enable_recommender=True //Default, try the new recommendation feature
$ az config set interactive.enable_recommender=False // Disable the recommendation feature
```

#### **[Add]** Add loading bar when initializing the az interactive
We added the loading bar to show the progress of the initialization. Initializing `az interactive` will take about 1min, with a default timeout of 150 seconds.

If the initialization is not finished within 150 seconds, the loading bar can be stopped and the initialization will continue in the background.

However, incomplete loading and initialization may result in some command parameters not being updated, some commands not being executed, etc. This can cause unknown errors, which will return to normal after loading is complete.
![loading_bar.gif](docs%2Floading_bar.gif)

#### **[Optimize]** Optimize the telemetry feedback to adapt to new recommendation function
In order to collect data and facilitate the optimization and tuning of the cli recommendation model, we have optimized the telemetry feedback function.

We have added `cli_recommendation_feedback` to the `properties` of telemetry feedback. For details, please refer to [cli-recommendation](https://github.com/hackathon-cli-recommendation/cli-recommendation/blob/master/Docs/feedback_design.md).


#### **[Add]** Added memory and completion mechanism for param value in scenarios

The completion mechanism for param value in scenarios is added to improve the completion ability of param value in scenarios.

In multiple commands of the same scenario, once the user enters a param value, we store the value entered by the user based on the scenario sample value and some special global params, and automatically recommend the completion of these param values in subsequent commands.

#### **[Add]** Recommending scenarios based on keywords and natural language
We have added the ability to recommend scenarios based on keywords and natural language. When the user enters a command, we will recommend the scenarios that are most likely to be used based on the keywords and natural language descriptions of the functions the user wants to implement.

```bash
$ az interactive // initialize the az interactive
$ /connect a mongodb to web app // Search for scenario by starting with / and entering keywords
>>  output
[1] Connect an app to MongoDB (Cosmos DB). (5 Commands)
Connect an app to MongoDB (Cosmos DB).

[2] Tutorial to create and connect Web App to Azure Database for MySQL Flexible Server in a virtual network (6 Commands)
Tutorial to create and connect Web App to Azure Database for MySQL Flexible Server in a virtual network

[3] Connect an app to SQL Database. (7 Commands)
Connect an app to SQL Database.

[4] Connect an app to a storage account. (5 Commands)
Connect an app to a storage account.

[5] Deploy an ASP.NET Core web app to Azure App Service and connect to an Azure SQL Database. (8 Commands)
Deploy an ASP.NET Core web app to Azure App Service and connect to an Azure SQL Database.

 ? Please select your option (if none, enter 0):
 $ 1 // Select the scenario you want to use
```
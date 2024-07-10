# GridDigger

[![GridDigger](https://github.com/The-Grid-Data/GridDigger/tree/railway)](https://github.com/The-Grid-Data/GridDigger/)

## Introduction

GridDigger is a Telegram bot that provides access to a complex Solana database (The Grid ID) by fetching data from its source and presenting it in a user-friendly manner. You can interact with GridDigger live [here](https://t.me/the_grid_id_bot).

## Goal

The goal behind GridDigger is to demonstrate the capabilities of The Grid ID search technology through an intuitive interface.

## Features

- **User-friendly interface**: Easy interaction via Telegram.
- **Real-time data**: Fetches the latest data from Grid ID.
- **GraphQL API**: Utilizes GraphQL for efficient data retrieval.

## API

GridDigger previously used a REST API and now has switched to GraphQL. It retrieves data directly from this public API: ```https://maximum-grackle-73.hasura.app/v1/graphql```

You can explore and play around with the API using this GraphiQL interface: [GraphiQL Playground](https://cloud.hasura.io/public/graphiql?endpoint=https://maximum-grackle-73.hasura.app/v1/graphql).

import { configureStore, createSlice } from '@reduxjs/toolkit'

const vectors = createSlice({
    name: 'vectors',
    initialState: {
        data: null,
        loading: true,
        error: null,
    },
    reducers: {
        setData: (state, action) => {
            state.data = action.payload;
            state.loading = false;
        },
        setError: (state,action) => {
            state.error = action.payload;
            state.loading = false;
        },
        setLoading: (state) => {
            state.loading = true;
        }
    }
})

export const { setData, setError, setLoading } = vectors.actions

const Store = configureStore({
    reducer: {
        dbs: vectors.reducer,
    }
})

export default Store;
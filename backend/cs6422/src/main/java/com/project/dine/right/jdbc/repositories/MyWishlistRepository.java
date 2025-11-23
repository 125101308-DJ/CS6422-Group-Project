package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.MyWishlist;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MyWishlistRepository extends CrudRepository<MyWishlist, Long> {

    @Query("select * from public.my_wishlist where user_id=:userId")
    List<MyWishlist> findByUserId(@Param("userId") Long userId);

    @Query("delete from public.my_wishlist where user_id=:userId and place_id=:restaurantId")
    void deleteByUserIdAndPlaceId(@Param("userId") Long userId, @Param("restaurantId") Long restaurantId);

}
